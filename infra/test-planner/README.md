This is the markdown for test planner.

# Install Node.js and NPM

## Step1: Download Node.js Installer & Run

Go to [Download | Node.js (nodejs.org)](https://nodejs.org/en/download/) , Click the **Windows Installer** button to download the latest LTS version. At the time this readme was written, version v16.14.2-x64 was the latest LTS version. The Node.js installer includes the NPM package manager.

Once the installer finishes downloading, launch it. All settings are default.

## Step2: Verify Installation

Open a command prompt (or PowerShell), and enter the following:

``node -v``

The system should display the Node.js version installed on your system. You can do the same for NPM:

``npm -v``

# Intall Linear programming helper tool & Run Test_Planner

## Linear programming helper tool Introduction:

Our Object-2 is actually a linear programming problem. And we use a open-source helper tool to help us. 

Objective-2 (Linear programming): https://github.com/JWally/jsLPSolver

## Install & Run Test_Planner

Step 1: Go the test folder by ``cd C:\Users\XXX\rainmaker\infra\test-planner`` (Replace XXX with your user name)

Step 2: Install solver: ``npm install javascript-lp-solver --save -g --prefix .\``

This step will create a folder called node_modules in current directory. The ``-g --prefix .\`` help we select current folder to intall solver.

If we do not specify by ``-g --prefix .\``, the solver will be installed in the directory specified by npm config's cwd.

You can check it by  `npm config list` , which will show you the config of npm.

Step 3: Run the the test_planner for objective - 0,1, 2, 3 &4: ``node lp_planner.js``

## Unintall the dependency

Step 1: Go the test folder by ``cd C:\Users\XXX\rainmaker\infra\test-planner`` (Replace XXX with your user name)

Step 2: Uninstall solver: ``npm uninstall -D javascript-lp-solver``

Step 3: Check if uninstall successfully: ``npm list``
