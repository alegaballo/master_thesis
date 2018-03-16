#!/bin/bash

routers=(r1 r2 r3 r4 r5 r6 ri1 ri2 ri3 ri4)
cmd="netstat -rn | sed -r \"s/ +/ /g\" | sed 1,2d | cut -f 1,2 -d \" \""


for router in "${routers[@]}"
do 
    route=`bash mx $router $cmd`
    echo $route | tr " " "\n" | xargs -n 2 echo $router
    echo 
done > routes.txt

