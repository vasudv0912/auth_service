from kafka import KafkaConsumer


consumer = KafkaConsumer('books', bootstrap_servers=['172.17.0.1:9091'])
for message in consumer:
    print (message)