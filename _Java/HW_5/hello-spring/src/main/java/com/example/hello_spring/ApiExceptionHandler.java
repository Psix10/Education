package com.example.hello_spring;

import java.util.Map;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<Map<String, Object>> handleStatus(
            ResponseStatusException exception
    ) {
        String message = exception.getReason() != null
                ? exception.getReason()
                : "Ошибка запроса";

        return ResponseEntity
                .status(exception.getStatusCode())
                .body(Map.of(
                        "status", exception.getStatusCode().value(),
                        "message", message
                ));
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<Map<String, Object>> handleConflict(
            DataIntegrityViolationException exception
    ) {
        return ResponseEntity.status(409).body(Map.of(
                "status", 409,
                "message",
                "Конфликт данных: имя пользователя занято "
                        + "или нарушено ограничение базы данных"
        ));
    }
}