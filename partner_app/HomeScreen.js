import React, { useState } from 'react';
import { StyleSheet, Text, View, Switch, TouchableOpacity } from 'react-native';

export default function HomeScreen() {
  const [isOnDuty, setIsOnDuty] = useState(false);
  const toggleSwitch = () => setIsOnDuty(previousState => !previousState);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome Partner</Text>
      <View style={styles.dutyContainer}>
        <Text style={styles.dutyText}>Off Duty</Text>
        <Switch
          trackColor={{ false: "#767577", true: "#81b0ff" }}
          thumbColor={isOnDuty ? "#f5dd4b" : "#f4f3f4"}
          ios_backgroundColor="#3e3e3e"
          onValueChange={toggleSwitch}
          value={isOnDuty}
        />
        <Text style={styles.dutyText}>On Duty</Text>
      </View>
      <TouchableOpacity style={[styles.statusButton, { backgroundColor: isOnDuty ? '#28a745' : '#dc3545' }]}>
        <Text style={styles.statusButtonText}>{isOnDuty ? 'You are On Duty' : 'You are Off Duty'}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
  },
  dutyContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 30,
  },
  dutyText: {
    fontSize: 18,
    marginHorizontal: 10,
  },
  statusButton: {
    width: '100%',
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 20,
  },
  statusButtonText: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },
});
