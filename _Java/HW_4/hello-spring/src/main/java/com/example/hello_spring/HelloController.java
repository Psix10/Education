package com.example.hello_spring;


import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;


@RestController
public class HelloController {
    private final MessageService service;

    public HelloController(MessageService service) {
        this.service = service;
    }

    @GetMapping("/messages")
    public Iterable<Message> getMessages() {
        return service.getAllMessages();
    }

    @PostMapping("/messages")
    @ResponseStatus(HttpStatus.CREATED)
    public Message createMessage(@RequestBody Message message) {
        return service.sendMessage(message.getContent(), message.getAuthor());
    }
    
}