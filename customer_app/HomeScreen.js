import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Switch } from 'react-native';

export default function HomeScreen({ navigation }) {
  const [isUrgent, setIsUrgent] = useState(false);
  const toggleSwitch = () => setIsUrgent(previousState => !previousState);

  const services = ['Dishwashing', 'Brooming', 'Cooking', 'Laundry'];

  return (
    <View style={styles.container}>
      <View style={styles.toggleContainer}>
        <Text style={styles.toggleText}>Schedule</Text>
        <Switch
          trackColor={{ false: "#767577", true: "#81b0ff" }}
          thumbColor={isUrgent ? "#f5dd4b" : "#f4f3f4"}
          ios_backgroundColor="#3e3e3e"
          onValueChange={toggleSwitch}
          value={isUrgent}
        />
        <Text style={styles.toggleText}>Urgent</Text>
      </View>
      <View style={styles.cardContainer}>
        {services.map((service, index) => (
          <TouchableOpacity key={index} style={styles.card}>
            <Text style={styles.cardText}>{service}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  toggleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    marginBottom: 20,
  },
  toggleText: {
    fontSize: 16,
    marginHorizontal: 10,
  },
  cardContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  card: {
    width: '48%',
    height: 150,
    backgroundColor: '#f0f0f0',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
  },
  cardText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});
