# acdsl_cli
`acdsl_cli` provides a command line interface to access shared link of Amazon Cloud Drive. It is inspired by [acd_cli](https://github.com/yadayada/acd_cli).

## Install
```
pip3 install --upgrade git+https://hwiorn@bitbucket.org/hwiorn/acdsl_cli.git
```
   or
```
sudo pip3 install --upgrade git+https://hwiorn@bitbucket.org/hwiorn/acdsl_cli.git
```

## Usage
### Listing
```
acdslcli list <shared link url> <path>
acdslcli ls <shared link url> <path>
```

#### Examples
```
acdslcli ls 'https://www.amazon.com/clouddrive/share/...' /
```

### Download
```
acdslcli download <shared link url> <path>
acdslcli download -r <shared link url> <path>
acdslcli dn <shared link url> <path>
acdslcli dn -r <shared link url> <path>
```

#### Examples
```
acdslcli download  'https://www.amazon.com/clouddrive/share/...' /
acdslcli download -r 'https://www.amazon.com/clouddrive/share/...' /
```

