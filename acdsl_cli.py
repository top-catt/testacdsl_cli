#!/usr/bin/env python3

import re, os.path
import argparse
import json
from urllib import request

__version__ = '0.0.3'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36'

def makePrettySize(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024:
            return '{:.1f}{}'.format(size, unit)
        size /= 1024

def effectiveDownload(url, filename, size, out_paths, ntries):
    assert ntries >= 1
    for _ in range(ntries):
        try:
            u = request.urlopen(url)

            with open(os.path.normpath(out_paths + '/' + filename), 'wb') as f:
                readn = 0
                BLOCK = 8192
                while True:
                    b = u.read(BLOCK)
                    if not b:
                        break

                    readn += len(b)
                    f.write(b)
                    print('> Downloading: %s Bytes: %d of %d (%2.3f%%) %s' % (filename, readn, size, readn/size * 100., makePrettySize(size)), end="\r")
                print()
            break
        except request as err:
            if not isinstance(err.reason, socket.timeout):
               raise
    else:
        raise err
  

def downloadFile(url, filename, size, out_paths):
    if not out_paths:
        out_paths = '.'

    if os.path.isfile(out_paths + '/' + filename):
        exsize = os.path.getsize(out_paths + '/' + filename)
        if exsize == size:
            print('File exist: %s \r' % filename)
        else:
            print('File exist but wrong size! Downloading...\r')
            effectiveDownload(url, filename, size, out_paths, 3)
    else:    
        effectiveDownload(url, filename, size, out_paths, 3)

class acd_slmain:
    def __init__(self):
        arg = argparse.ArgumentParser()
        arg.add_argument('-v', '--verbose')
        arg.add_argument('--region', help='Amazon region (com, it, fr..)', default='co.uk')
        subargs = arg.add_subparsers()
        subarg = subargs.add_parser('list', help = 'listing files', aliases=['ls'])
        subarg.add_argument('url', help='shared link')
        subarg.add_argument('path', help='path')
        subarg.set_defaults(func=self.list)

        subarg = subargs.add_parser('download', help = 'download files', aliases=['dn'])
        subarg.add_argument('-r', '--recursive', action='store_true', help='download files recusively')
        subarg.add_argument('url', help='shared link')
        subarg.add_argument('path', help='path')
        subarg.set_defaults(func=self.download)

        args = arg.parse_args()
        if hasattr(args, 'func'):
            args.func(args)

    def _list(self, url, path, region):
        try:
            slmeta = acd_slmeta(url)
            co = slmeta.getCollections(region)

            # Find path
            items = co.getItems()
            for p in path:
                n = [it for it in co.getItems() if it['name'] == p]
                if not n:
                    raise Exception('No such path or file name: %s' % p)

                if n[0]['directory']:
                    co = co.getChildren(n[0]['id'], region)
                    items = co.getItems()
                else:
                    items = [n[0]]
                    break

            return items
        except Exception as e:
            print('Error while listing directory: ' + str(e))

        return []

    def list(self, args):
        print("Region selected with --region parameter: amazon."+args.region)
        url = args.url.replace('/clouddrive/share/', '/drive/v1/shares/') # Replace API url
        url = '{}?resourceVersion=V2&ContentType=JSON&asset=ALL'.format(url)
        path = [p for p in args.path.split('/') if p.strip()]
        items = self._list(url, path, args.region)

        for it in items:
            if it['directory']:
                print('[{}]'.format(it['name']))
            else:
                print('{}\t{}'.format(it['name'], makePrettySize(it['size'])))

    def _download(self, url, path, recursive, region, outpath=[]):
        items = list(self._list(url, path, region))

        paths = '/'.join(outpath)
        if paths and not os.path.exists(paths):
            os.makedirs(paths)

        for it in [x for x in items if not x['directory']]:
            downloadFile(it['link'], it['name'], it['size'], paths)

        if not recursive:
            return

        for it in [x for x in items if x['directory']]:
            self._download(url, path + [it['name']], recursive, region, outpath + [it['name']])

    def download(self, args):
        print("Region selected with --region parameter: amazon."+args.region)
        url = args.url.replace('/clouddrive/share/', '/drive/v1/shares/') # Replace API url
        url = '{}?resourceVersion=V2&ContentType=JSON&asset=ALL'.format(url)
        path = [p for p in args.path.split('/') if p.strip()]
        self._download(url, path, args.recursive, args.region)

class acd_slmeta:
    def __init__(self, url):
        req = request.Request(url)
        req.add_header('User-Agent', USER_AGENT)

        resp = request.urlopen(req)
        if resp.code != 500:
            raise Exception('This url is not seems to be shared link')

        self.data = json.loads(resp.read().decode())
        self.id = self.data['nodeInfo']['id']
        self.shareId = self.data['shareId']

    def __str__(self):
        if self.data:
            return('Node Info\n> Name: {}\n> Created Date: {}\n> Modified Date: {}\n> Id: {}\n> Share Id: {}\n> Share URL: {}'.format(
                self.data['nodeInfo']['name'],
                self.data['nodeInfo']['createdDate'],
                self.data['nodeInfo']['modifiedDate'],
                self.data['nodeInfo']['id'],
                self.data['shareId'],
                self.data['shareURL']
            ))

    def getCollections(self, region):
        if not self.id or not self.shareId:
            return None

        return acd_collection('https://www.amazon.'+region+'/drive/v1/nodes/{}/children?resourceVersion=V2&ContentType=JSON&limit=500&sort=%5B%22kind+DESC%22%2C+%22modifiedDate+DESC%22%5D&asset=ALL&tempLink=true&shareId={}'.format(self.id, self.shareId), self.shareId)

class acd_collection:
    def __init__(self, url, shareId):
        req = request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        resp = request.urlopen(req)
        if resp.code != 500:
            raise Exception('This url is not seems to be shared link')

        self.data = json.loads(resp.read().decode())
        self.shareId = shareId

    def __str__(self):
        if self.data:
            s = 'Collection Info\n'
            for item in self.getItems():
                fmt = '> {}\t{}\t{}\n'
                if item['directory']:
                    fmt = '> [{}]\t{}\t{}\n'

                s += fmt.format(item['name'], item['id'], item['link'])

            return s

    def getItems(self):
        if not self.data:
            yield Exception('No items')

        for x in self.data['data']:
            yield {
                'name': x['name'],
                'directory': x['kind'] == 'FOLDER',
                'createdDate': x['createdDate'],
                'modifiedDate': x['modifiedDate'],
                'id': x['id'],
                'version': x['version'],
                'link': x['tempLink'] if 'tempLink' in x else '',
                'size': x['contentProperties']['size'] if 'contentProperties' in x else 0,
                'md5': x['contentProperties']['md5'] if 'contentProperties' in x else '',
            }

    def getChildren(self, id, region):
        if not self.data:
            return None

        return acd_collection('https://www.amazon.'+region+'/drive/v1/nodes/{}/children?resourceVersion=V2&ContentType=JSON&limit=500&sort=%5B%22kind+DESC%22%2C+%22modifiedDate+DESC%22%5D&asset=ALL&tempLink=true&shareId={}'.format(id, self.shareId), self.shareId)

def main():
    acd_slmain()

if __name__ == '__main__':
    main()

