if ping -q -c 10 -W 1 8.8.8.8 >/dev/null; then
  echo "IPv4 is up"
else
  ifconfig wlan0 down
  sleep 5
  ifconfig wlan0 up
fi