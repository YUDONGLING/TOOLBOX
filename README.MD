# General Dev ToolBox for Python, PHP & (EdgeRuntime) JavaScript
For Git Repository, to add ToolBox as a submodule, use Git and run:
```
cd "{%ThePathOfGitRepository%}"
git submodule add "https://github.com/YUDONGLING/TOOLBOX.git" "Pkg"
```
For Git Repository, to checkout ToolBox, use Git and run:
```
git submodule init
git submodule update
```
For Windows Filesystem, use CMD and run:
```
mklink /j "{%ThePathYouLikeToUseToolBox%}\Pkg" "{%ThePathOfTheToolBox%}"
```
For MacOS Filesystem, use Termail and run:
```
ln -s {%ThePathOfTheToolBox%} {%ThePathYouLikeToUseToolBox%}/Pkg
```
