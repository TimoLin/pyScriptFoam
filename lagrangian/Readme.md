Tutorial for ParticleStatistic  

```cpp
CloudFunctions
{
    x1
    {
        type            particleStatistic;
        mode            concentricCircle;
        origin          (0.105 0.0 0.0);
        radius          (0.021);
        nSector         1;
        refDir          (1 0 0);
        normal          (1 0 0);

        surfaceFormat   raw;
        maxStoredParcels 200000;
        resetOnWrite    yes;
    }

    x2
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
        maxStoredParcels 200000;
        resetOnWrite    yes;
    }    
}
```
