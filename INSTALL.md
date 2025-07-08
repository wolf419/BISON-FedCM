# Build Instructions

## 1. Install depot_tools 

https://chromium.googlesource.com/chromium/src/+/main/docs/linux/build_instructions.md#install

## 2. Get the code

```
mkdir ~/chromium && cd ~/chromium
```

```
fetch --nohooks chromium
```

```
cd src
```

```
git checkout 0e2b5d09144f327ab3283051151208d7c7541753
```

```
git apply /path/to/bison.patch
```

## 3. Install additional build dependencies

```
./build/install-build-deps.sh
```

## 4. Sync dependencies and run hooks

```
gclient sync
```

## 5. Setting up the build

```
gn args out/Default
```

This will bring up an editor. Enter:

```
is_debug = false
```

## 6. Build Chromium

```
autoninja -C out/Default chrome
```

## 7. Run Chromium

```
out/Default/chrome
```
