# Data Streaming & Visualization Workshop 

## Use Case: Manufacturing Robot Predictive Maintenance

### Problem Definition:
Our manufacturing facility is experiencing substantial downtime owing to torque tube failures in material
handling robots, resulting in 480 minutes of unscheduled downtime per occurrence. The primary reason is due to 
equipment aging, and we lack the necessary technologies to monitor equipment health proactively.


##  👥 Team Members: 
	1. Edwin Lopez Castañeda
    2. Jiho Jun
    3. Jarius Bedward
    4. Vishnu Sivaraj


##  🚀 System Architecture:
Our predictive maintenance solution is built with the following architecture

1. **Data Source**: Simulated robot controller data stream (CSV file)
2. **Data Collection Layer**: Python-based "StreamingSimulator" class
3. **Data Persistence Layer**: **Neon** (serverless PostgreSQL) database
4. **Application Layer**: Jupyter Notebook for processing and analysis 
5. **Visualization Layer**: Real-time Matplotlib dashboard



## 📋 Requirements
- Python 3.1 or 03.12
- Jupyter Notebook
- Pandas 2.3.2, Matplotlib, Seaborn
- psycopg2` or `psycopg2-binary` package for PostgreSQL connection
- An active **Neon.tech** project and database connection string
- Add any other specific dependencies

##  🎯  How to Run

1. Clone this repo
2. Install Required Dependencies: "pip install -r requirements.txt"
3. **Neon Setup**:  
    - Create a free account at [Neon.tech](https://neon.tech)
    - Create a new project and database
    - Retrieve your connection string from the Neon Dashboard
4. In the program, create an env file 
5. In the env file add the connection string from Neon: ex): DATABASE_URL=postgresql: ~ require
6. Run the Jupyter notebook cells sequentially 
7. The dashboard will display real time metrics updated every 2 seconds

    
## Licence


##  🤝 Contributing 
This is a workshop developed for CSNC8010. If any questions arise do not hesitate 
to contact the mentioned team members.