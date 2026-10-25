package com.example.hello_spring;

import java.util.Comparator;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Repository;

@Repository
public class MessageRepository {
    private final ConcurrentHashMap<Long, Message> storage = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    public Message save(Message message) {
        if (message.getId() == null) {
            message.setId(idCounter.incrementAndGet());
        }
        storage.put(message.getId(), message);
        return message;
    }

    public Optional<Message> findByIdMessage(Long id) {
        return Optional.ofNullable(storage.get(id));
    }

    public Iterable<Message> findAll() {
        return storage.values().stream()
                .sorted(Comparator.comparing(Message::getId).reversed())
                .limit(30)
                .toList();
    }

    public void deleteById(Long id) {
        storage.remove(id);
    }

    public void clear() {
        storage.clear();
    }
}