find -name "*.err" | xargs -I {} rm {}
find -not -path "./Docs/*" -not -path "./Drawings/*" -name "*.3d" | xargs -I {} rm {}

