# Readme.md
This archive contains source code of my genetic algorithm.
To run it you should have docker installed.
First, start the docker daemon, then open terminal in the ```code/``` folder.
Run 
```
docker build -t iai2.
```
After the build finishes (it will take few minutes), run 
```
docker run -it -v ~/.output:/app/output iai2.
```
If you want to add your own input images, you can place them inside the 
```input/``` folder, rebuild the container.
Note, that they should be named unnamed*.png, where * is number from 1 to 10. Also the file unnamed.png (without number) should be present in input folder.\
Output will be placed at ```.output/``` folder.

...

If the docker way does not work, you can install requirements from 
```code/requirements.txt``` and run it by invoking ```launch.sh``` script, or ```python3 main.py```