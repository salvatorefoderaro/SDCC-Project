sudo apt install xterm
xterm -title "Proxy" -hold -e "cd ../Proxy_Python; sh run.sh"  &
xterm -title "Client 1" -hold -e "cd ../IoT; sh run.sh 'config/config1.json'"  &
xterm -title "Client 2" -hold -e "cd ../IoT; sh run.sh 'config/config2.json'"  &
xterm -title "Client 3" -hold -e "cd ../IoT; sh run.sh 'config/config3.json'"  &
xterm -title "Client 4" -hold -e "cd ../IoT; sh run.sh 'config/config4.json'"  &
xterm -title "Client 5" -hold -e "cd ../IoT; sh run.sh 'config/config5.json'"  &
xterm -title "Client 6" -hold -e "cd ../IoT; sh run.sh 'config/config6.json'"  &
xterm -title "Client 7" -hold -e "cd ../IoT; sh run.sh 'config/config7.json'"  &
xterm -title "Client 8" -hold -e "cd ../IoT; sh run.sh 'config/config8.json'"  &