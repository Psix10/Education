package com.example.hello_spring;

import java.util.Objects;

public class Message {
    private Long id;
    private String content;
    private String author;

    // Конструкторы
    public Message() {}
    public Message(String content, String author) { 
        this.content = content;
        this.author = author;
    }
    
    // Геттеры и сеттеры
    public Long getId() { return id;}
    public void setId(Long id) { this.id = id;}

    public String getContent() {return content;};
    public void setContent(String content) { this.content = content; }

    public String getAuthor() { return author; }
    public void setAuthor(String author) { this.author = author; }
    
    // equals() и hashCode()
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;

        Message message = (Message) o;
        return Objects.equals(id, message.id) && Objects.equals(content, message.content) && Objects.equals(author, message.author);
    }

    @Override
    public int hashCode(){
        return Objects.hash(id, content, author);
    }

    @Override
    public String toString() {
        return "Message{" + "id=" + id + ", content='" + content + '\'' + ", author='" + author + '}';
    }
}
