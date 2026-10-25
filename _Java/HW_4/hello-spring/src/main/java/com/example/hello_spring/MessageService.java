package com.example.hello_spring;

import org.springframework.stereotype.Service;


@Service
public class MessageService {
    private final MessageRepository repository;

    public MessageService(MessageRepository repository){
        this.repository = repository;
        initializeSampleData();
    }

    private void initializeSampleData() {
        repository.save(new Message("Hello, Spring!", "Bot"));
        repository.save(new Message("In-memory storage works", "Bot"));
        for (int i = 1; i < 30; i++){
            repository.save(new Message("" + i, "Generation"));
        }
    }

    public Iterable<Message> getAllMessages() {
        return repository.findAll();
    }

    public Message sendMessage(String message, String author) {
        return repository.save(new Message(message, author));
    }
}

