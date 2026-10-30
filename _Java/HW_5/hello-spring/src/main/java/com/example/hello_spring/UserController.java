package com.example.hello_spring;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/users")
public class UserController {

    private final JdbcUserRepository repository;

    public UserController(JdbcUserRepository repository) {
        this.repository = repository;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public User create(@RequestBody CreateUserRequest request) {
        if (request == null
                || request.username() == null
                || request.username().isBlank()
                || request.username().strip().length() > 100) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "username должен содержать от 1 до 100 символов"
            );
        }

        return repository.save(request.username().strip());
    }

    @GetMapping("/{id}")
    public User getById(@PathVariable("id") Long id) {
        if (id <= 0) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "ID должен быть положительным числом"
            );
        }

        return repository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Пользователь с ID " + id + " не найден"
                ));
    }
}