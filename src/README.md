image repo.


workaround to fix ffmpeg corrupts generated gif quality by first extracting palette, and then use that palette to generate gif.
```
ffmpeg -i image_%02d.png -vf palettegen palette.png
ffmpeg -i image_%02d.png -i palette.png -lavfi paletteuse video.gif
```
