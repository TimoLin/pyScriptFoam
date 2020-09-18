A simple tutorial for `ParticleStatistic` CloudFunction.
=======

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
