# Basic Application

This web application allows you to vote for candidates in an election. In this version of the app, the names of the candidates have been hard coded into the HTML template, but populating them from a dynamic list in the database is not that hard as well.

To vote for the candidate, enter your public key (voter id) and private key. Once the keys have been verified inside the node, you need to press the mine block button to actually mine the block. 

Before the block is mined, we check if the person has voted before and use ZKP to prove that we have knowledge of the person we are voting for without revealing the stance of our vote. You can see your vote by clicking the my vote button.

# To Do

0. Database and generation of RSA Public and Private Keys
1. User Authentication (RSA)
2. Create web app
3. Integrate web app with backend APIs