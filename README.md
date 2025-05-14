# Project-Tracker
Crypto Tracker version 1.0: tracks coins, shows warm and cold storage, stocks and reads csv from exchange.

![Main](https://github.com/user-attachments/assets/66392301-6016-40cc-86ad-9a1303684241)

Still work in progress. Fully functional version. Written in Python. Run from the commandline or use 
auto-py-to-exe to make an excutable (Windowss). Still a lot of work to be done. Feel free to use and experiment. 
I had to learn Python for it but with help of Gemin, Co-pilot and Chatgtp it was a start for an intresting experience. 
To make a Crypto Fear and Greed index with AI is, at the least, an adventure. It gave an insight in how to formulate a 
better prompt. It took a few hours to explain that fear and greed was positioned correctly but the colors where just
wrong and on the wrong side.

If you use the program and make adjustments, please let me know. Woukd like to learn. 

Main program: tracker.py needs tracker.xlsx
sub programs:
  - calcpiv.py (load and calculte csv-file)
  - README.MD

**Main program **
Will start with the price of BTC in EUR and Dollars; Shows the latest ATH.  Will refresh every 30 seconds

**Option Warm Storage**
Gets the coins from the exchange and shows all the coins from the exchange with coin name, rate (in EUR), amount and current vakue (in EUR). 
Connection with the exchange depends on the tracker.xlsx sheet Credentials. Fill in the shortname of the exchange, Key, Secret Key and URL. 
Screen refreshes every 20 seconds

**Option Cold Storage** 
Gets thwe coins from tracker.xlsx sheet Cold_Storage where the user has put in the coinname and the amount. 
Will show all the coins from the exchange with coin name, rate (in EUR), amount and current vakue (in EUR)
Screen refreshes every 20 seconds.

**Option Input Stocks**
Currently still working on the api for this. Option is currently manual, and asks for the total stock value. 
If used, it will be shown on the total assets screen

**Option Total Assets**
Shows Warm Storage, Cold Storage, Stock (if available) and gives Total Assets. If a csv file has been read and calculated
it will show the amount of money put in the exchange, the amount money taken out of the exchange The current Total Invest 
and the Profit/loss

**Live View Fear and Greed**
Shows the current Crypto Fear and Greed index graphically, with a bit of animation. Shows also the index from yesterday, last week and last month


![fearandgreed](https://github.com/user-attachments/assets/af312a20-f8fa-4246-aecf-aeb87a45e75d)


**Live View AGGR**
Opens een AGGR window and shows the progress of the value of Bitcoin. 

![AggrViewer](https://github.com/user-attachments/assets/11c0098f-115e-402f-9b89-79704f26091b)



**Live View Mempool**

