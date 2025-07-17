# Build Instructions

## 1. Install depot_tools 

https://chromium.googlesource.com/chromium/src/+/main/docs/linux/build_instructions.md#install

## 2. Get the chromium source code

```
mkdir ~/chromium && cd ~/chromium
```

```
fetch --nohooks --no-history chromium
```

```
cd src
```

## 3. Checkout a specific commit

```
git fetch --unshallow
```

```
git checkout 0e2b5d09144f327ab3283051151208d7c7541753
```

```
gclient sync --nohooks
```

Repeat until no errors occur


## 4. Apply your patch

```
git apply /path/to/bison.patch
```

## 5. Install additional build dependencies

```
./build/install-build-deps.sh
```

## 6. Sync dependencies and run hooks

```
gclient sync
```

## 7. Setting up the build

```
gn args out/Default
```

This will bring up an editor. Enter:

```
is_debug = false
```

## 8. Build Chromium

```
autoninja -C out/Default chrome
```

## 9. Run Chromium

```
out/Default/chrome
```
