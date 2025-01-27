## Version 1.4.0 (2025/01/27)

### Issues Closed

* [Issue 38](https://github.com/storpipfugl/pykdtree/issues/38) - pydktree breaks down for very large number of data points ([PR 135](https://github.com/storpipfugl/pykdtree/pull/135) by [@lkeegan](https://github.com/lkeegan))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 126](https://github.com/storpipfugl/pykdtree/pull/126) - Fix the wrong syntax of pip install

#### Features added

* [PR 135](https://github.com/storpipfugl/pykdtree/pull/135) - Add automatic switching between 32-bit and 64-bit structures depending on number of points ([38](https://github.com/storpipfugl/pykdtree/issues/38), [38](https://github.com/storpipfugl/pykdtree/issues/38))

In this release 2 pull requests were closed.


## Version 1.3.13 (2024/09/04)

### Issues Closed

* [Issue 116](https://github.com/storpipfugl/pykdtree/issues/116) - Segmentation fault on empty points ([PR 119](https://github.com/storpipfugl/pykdtree/pull/119) by [@STNLd2](https://github.com/STNLd2))

In this release 1 issue was closed.

### Pull Requests Merged

#### Bugs fixed

* [PR 119](https://github.com/storpipfugl/pykdtree/pull/119) - Fixed empty pts segfault ([116](https://github.com/storpipfugl/pykdtree/issues/116))

#### Features added

* [PR 124](https://github.com/storpipfugl/pykdtree/pull/124) - Enable Python 3.13 wheel building and switch to C17 C standard

In this release 2 pull requests were closed.



## Version 1.3.12 (2024/04/12)

### Pull Requests Merged

#### Features added

* [PR 113](https://github.com/storpipfugl/pykdtree/pull/113) - Build against numpy 2.0rc1

In this release 1 pull request was closed.


## Version 1.3.11 (2024/02/15)

### Issues Closed

* [Issue 106](https://github.com/storpipfugl/pykdtree/issues/106) - Gotchas when installing on MacOS ([PR 107](https://github.com/storpipfugl/pykdtree/pull/107) by [@djhoese](https://github.com/djhoese))

In this release 1 issue was closed.

### Pull Requests Merged

#### Features added

* [PR 109](https://github.com/storpipfugl/pykdtree/pull/109) - Build wheels with numpy 2
* [PR 107](https://github.com/storpipfugl/pykdtree/pull/107) - Add OpenMP warning when extension fails to import ([106](https://github.com/storpipfugl/pykdtree/issues/106))

In this release 2 pull requests were closed.


## Version 1.3.10 (2023/11/29)

### Pull Requests Merged

#### Bugs fixed

* [PR 102](https://github.com/storpipfugl/pykdtree/pull/102) - Switch to Cython 3 in build process

In this release 1 pull request was closed.


## Version 1.3.9 (2023/09/22)

### Pull Requests Merged

#### Features added

* [PR 98](https://github.com/storpipfugl/pykdtree/pull/98) - Switch to cibuildwheel for wheel building

In this release 1 pull request was closed.


## Version 1.3.8 (2023/09/21)


## v1.3.6

Fix Python 3.11 compatibility and build Python 3.11 wheels

## v1.3.5

Build Python 3.10 wheels and other CI updates

## v1.3.4

Fix Python 3.9 wheels not being built for linux

## v1.3.3

Add compatibility to python 3.9

## v1.3.2

Change OSX installation to not use OpenMP without conda interpreter

## v1.3.1

Fix masking in the "query" method introduced in 1.3.0

## v1.3.0

Keyword argument "mask" added to "query" method. OpenMP compilation now works for MS Visual Studio compiler

## v1.2.2

Build process fixes

## v1.2.1Fixed OpenMP thread safety issue introduced in v1.2.0

## v1.2.0

64 and 32 bit MSVC Windows support added

## v1.1.1

Same as v1.1 release due to incorrect pypi release

## v1.1

Build process improvements. Add data attribute to kdtree class for scipy interface compatibility

## v1.0

Switched license from GPLv3 to LGPLv3

## v0.3

Avoid zipping of installed egg

## v0.2

Reduced memory footprint. Can now handle single precision data internally avoiding copy conversion to double precision. Default leafsize changed from 10 to 16 as this reduces the memory footprint and makes it a cache line multiplum (negligible if any query performance observed in benchmarks). Reduced memory allocation for leaf nodes. Applied patch for building on OS X.

## v0.1

Initial version.
