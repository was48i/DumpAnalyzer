# DumpAnalyzer
Compare the similarity between crash dump files based on AST, and analyze syntax tree using Python bindings for Clang.
## Install
### LLVM
We should install [Clang](http://releases.llvm.org/download.html) first:

![](https://raw.githubusercontent.com/ICHIGOI7E/mdpics/master/DumpAnalyzer/llvm.jpg)
### Python
Tested by [Python 3.6.8](https://www.python.org/downloads/release/python-368/)

Install required packages:
```
$ pip install -r requirements.txt
```
We parsing C++ in Python with Clang:

![](https://raw.githubusercontent.com/ICHIGOI7E/mdpics/master/DumpAnalyzer/python_clang.jpg)
### Source Code
Put prepared source code in specified directory.
## Usage
View help information:
```
$ ./src/analyze.py --help
```
If source code is updated, we need to update database:
```
$ ./src/analyze.py --update
```
Change the path of source code or dump files:
```
$ ./src/analyze.py --source [repo path]
```
```
$ ./src/analyze.py --dump [dump files]
```
Change the mode of analysis:
```
$ ./src/analyze.py --mode [ast/csi]
```
## Validation
We validate our classifier based on [confusion matrix](https://en.wikipedia.org/wiki/Confusion_matrix).

Our data set is cleaned and reshaped:

![](https://raw.githubusercontent.com/ICHIGOI7E/mdpics/master/DumpAnalyzer/validation.jpg)

Use the stats mode:
```
$ ./src/analyze.py --stats
```
## Contributing
We love contributions! Before submitting a Pull Request, it's always good to start with a new issue first.
### Contributors
[@was48i](https://github.com/was48i)

[@Pal1998](https://github.com/Pal1998)
## License
This library is licensed under Apache 2.0. Full license text is available in [LICENSE](https://github.com/ICHIGOI7E/DumpAnalyzer/blob/master/LICENSE).
