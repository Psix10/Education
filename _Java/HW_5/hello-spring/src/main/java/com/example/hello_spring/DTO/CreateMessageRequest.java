package com.example.hello_spring;

public record CreateMessageRequest(
        String content,
        Long authorId
) {
}