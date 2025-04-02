#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##################################################
#
# Boxer Management
#
##################################################

create_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Creating boxer $name..."
  curl -s -X POST "$BASE_URL/create-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer $name created successfully."
  else
    echo "Failed to create boxer $name."
    exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by name ($boxer_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$boxer_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by name ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (Name $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by name ($boxer_name)."
    exit 1
  fi
}

##################################################
#
# Fight Simulation
#
##################################################

create_fight() {
  boxer_1_id=$1
  boxer_2_id=$2

  echo "Starting fight between boxer $boxer_1_id and boxer $boxer_2_id..."
  response=$(curl -s -X POST "$BASE_URL/start-fight" -H "Content-Type: application/json" \
    -d "{\"boxer_1_id\":$boxer_1_id, \"boxer_2_id\":$boxer_2_id}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight started successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Fight result JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to start fight."
    exit 1
  fi
}

get_leaderboard() {
  sort_by=$1

  echo "Getting leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/get-leaderboard?sort_by=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard."
    exit 1
  fi
}

##################################################
#
# Run the tests
#
##################################################

# Health check
check_health

# Database check
check_db

# Create two boxers
create_boxer "Mike Tyson" 220 72 80 30
create_boxer "Muhammad Ali" 210 74 81 30

# Get boxers by ID and Name
get_boxer_by_name "Mike Tyson"
get_boxer_by_id 1

# Simulate a fight between two boxers
create_fight 1 2

# Get the leaderboard
get_leaderboard "wins"

# Clean up - delete the created boxers
delete_boxer_by_id 1
delete_boxer_by_id 2
