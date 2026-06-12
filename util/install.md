# Check serial on GPIO ports in Raspberry

## Installation

```bash
sudo apt-get update
sudo apt-get install -y python3-setuptools python3-full wget make gcc

wget https://github.com/joan2937/pigpio/archive/refs/tags/v79.tar.gz
tar zxf v79.tar.gz
cd pigpio-79; make; sudo make install

sudo ldconfig
sudo systemctl daemon-reload
sudo systemctl enable --now pigpiod

sudo systemctl status pigpiod
```

