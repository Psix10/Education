package com.example.hello_spring;

import java.util.List;

public record PageResponse<T>(
        List<T> content,
        int page,
        int size,
        long totalElements,
        long totalPages
) {
}