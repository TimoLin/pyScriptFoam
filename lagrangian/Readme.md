A simple tutorial for `ParticleStatistic` CloudFunction.
=======

## particleStatistic.py
### Usage
```
usage: particleStatistic.py [-h] [--process] [--time TIME] --diameter DIAMETER
                            --rMax RMAX [--sizeGroup SIZEGROUP]
                            [--origin ORIGIN] [--norm {100,010,001}] [--pdf]
                            [--csv] [--tecplot]

Post-Processing sampled Lagrangian data from CloudFunction:ParticleStatistic.

optional arguments:
  -h, --help            show this help message and exit
  --process             Post-process sampled lagrangian data and get radial profiles
  --time TIME           Time ranges
  --diameter DIAMETER   Normalized Reference diamter or length for the case (mm)
  --rMax RMAX           Max radial location of the spray data (mm)
  --sizeGroup SIZEGROUP Diameter groups for conditioned properties (um)
  --origin ORIGIN       Co-ordinate of the injector's center
  --norm {100,010,001}  Normal direction of the plane (default: 100)
  --pdf                 Get droplete droplet size PDF and volume PDF for sampled planes
  --csv                 Output in csv format
  --tecplot             Output in Tecplot ascii format
```
### Script samples
Use `--csv` or `--tecplot` according to your needs. 

- For simple cases
```
python3 ~/github/pyScriptFoam/lagrangian/particleStatistic.py --process --csv --diameter 1 --sizeGroup '10,20,30,40,50,60,70' --norm 001  --rMax 20
```

- For cases with origin not lying on the main axis
```
python3 ~/github/pyScriptFoam/lagrangian/particleStatistic.py --process --diameter 1 --rMax 20 --sizeGroup "20,40,60,80,100" --origin "0.087,0.10827,0" --norm "100" --tecplot
```


## ParticleStatistic CloudFunction
Here are two examples:  
(should be added in `cloudFunctions`  in file `sprayCloudProperties` or other CloudProperties that you use!)

## ConcentricCircle (圆形截面)
```c
    particleStatistic1
    {
        type            particleStatistic;
        mode            concentricCircle;
        origin          (0.105 0.0 0.0);
        radius          (0.021);
        nSector         1;
        refDir          (1 0 0);
        normal          (1 0 0);

        surfaceFormat   raw;
        maxStoredParcels 200;
        resetOnWrite    yes;
    }
```
## Polygon (多边形)- triangle, rectangle, square ...
```c
    particleStatistic2
    {
        type            particleStatistic;
        mode            polygon;
        polygons
        (
            (
                (0.105  0.021  0.021)
                (0.105  0.021 -0.021)
                (0.105 -0.021  0.021)
                (0.105 -0.021 -0.021)
            )    
        );
        normal          (1 0 0);

        surfaceFormat   raw;
        maxStoredParcels 200;
        resetOnWrite    yes;
    }
```
As you can see, `radius` and `polygons` in each functions are defined as a list - which means it accepts multiple radius and polygons in one  cloudfunction.  Like below:
```c
radius (0.021 0.025 0.03)
```
```c
polygons
(
      (
           (0.105  0.021  0.021)
          (0.105  0.021 -0.021)
          (0.105 -0.021  0.021)
          (0.105 -0.021 -0.021)
       )
       (
           (0.210  0.021  0.021)
           (0.210  0.021 -0.021)
           (0.210 -0.021  0.021)
           (0.210 -0.021 -0.021)
       )
);
```
But to avoid confusion when post-processing. It's recommended to define **only one radius**  or **only one polygon** when use this function, as the first two examples.

```
