find -name "*.err" | xargs -I {} rm {}
find -not -path "./Docs/*" -name "*.3d" | xargs -I {} rm {}

