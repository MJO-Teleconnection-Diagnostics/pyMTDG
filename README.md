# MJO-Teleconnections Diagnostics Package

This repository contains the user interface and code to run the diagnostics for evaluating the MJO teleconnections forecasted by a subseasonal to seasonal system. For the background information on diagnostics see: 

Stan, C., C. Zheng, E. K.-M. Chang, D. I. V. Domeisen, C. Garfienkel, A. M. Jenney, H. Kim, Y.-K. Lim, H. Lin, A. Robertson, C. Schwartz, F. Vitart, J. Wang, P. Yadav, 2022: Advances in the prediction of MJO-Teleconnections in the S2S forecast systems. Bulletin of the American Meteorological Society, 103, E11427-E1447. https://doi.org/10.1175/BAMS-D-21-0130.1

Contents:
1. [Software requirements](#introduction)
2. [Obtaining the code](#code)

## 1. Software requirements <a name="introduction"></a>
Some text

## 2. Obtaining the code <a name="code"></a>
To checkout and run the code, no git knowledge is required. To obtain the code you need to do the following:

a. Clone the repository.

  a.1 Clone the repository: master and all other branches
~~~
git clone https://github.com/cristianastan2/MJO-Teleconnections.git MJO-Teleconnections
~~~

  a.2 Clone the repository and fetch only a single branch
~~~
git clone --branch develop --single-branch  https://github.com/cristianastan2/MJO-Teleconnections.git MJO-Teleconnections
~~~

This will create a directory `MJO-Teleconnections/` in your current working directory.

b. Go into the newly created MJO-Teleconnections repository to create the environment required to run the package from the `mjo_telecon.yml` file included in the pckage.
~~~
cd MJO-Teleconnections
conda env create -n mjo_telecon -- file mjo_telecon.yml
~~~

c. Go to the `driver` directory to run the code.
~~~
cd driver
python mjo_gui.py
~~~
