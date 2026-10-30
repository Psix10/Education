package com.example.hello_spring;

import java.time.LocalDateTime;
import java.util.Objects;

public class Message {

    private Long id;
    private String content;
    private Long authorId;
    private LocalDateTime createdAt;

    public Message() {
    }

    public Message(String content, Long authorId) {
        this.content = content;
        this.authorId = authorId;
    }

    public Message(
            Long id,
            String content,
            Long authorId,
            LocalDateTime createdAt
    ) {
        this.id = id;
        this.content = content;
        this.authorId = authorId;
        this.createdAt = createdAt;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Long getAuthorId() {
        return authorId;
    }

    public void setAuthorId(Long authorId) {
        this.authorId = authorId;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }

        if (o == null || getClass() != o.getClass()) {
            return false;
        }

        Message message = (Message) o;

        return Objects.equals(id, message.id)
                && Objects.equals(content, message.content)
                && Objects.equals(authorId, message.authorId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, content, authorId);
    }

    @Override
    public String toString() {
        return "Message{" +
                "id=" + id +
                ", content='" + content + '\'' +
                ", authorId=" + authorId +
                ", createdAt=" + createdAt +
                '}';
    }
}