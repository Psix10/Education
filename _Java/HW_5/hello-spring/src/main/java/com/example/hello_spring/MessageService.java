package com.example.hello_spring;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class MessageService {

    private final JdbcMessageRepository messages;
    private final JdbcUserRepository users;

    public MessageService(
            JdbcMessageRepository messages,
            JdbcUserRepository users
    ) {
        this.messages = messages;
        this.users = users;
    }

    public Message getById(Long id) {
        requirePositiveId(id);

        return messages.findById(id)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Сообщение с ID " + id + " не найдено"
                ));
    }

    public PageResponse<Message> getMessages(
            int page,
            int size,
            Long authorId
    ) {
        if (page < 0 || size < 1 || size > 100) {
            throw badRequest(
                    "page должен быть >= 0, size — от 1 до 100"
            );
        }

        if (authorId != null) {
            requireUser(authorId);
        }

        long total = messages.count(authorId);
        long offset = (long) page * size;
        long totalPages = total / size + (total % size == 0 ? 0 : 1);

        return new PageResponse<>(
                messages.findPage(size, offset, authorId),
                page,
                size,
                total,
                totalPages
        );
    }

    @Transactional
    public Message create(CreateMessageRequest request) {
        validateMessage(request);
        requireUser(request.authorId());

        return messages.save(request);
    }

    @Transactional
    public int createBatch(List<CreateMessageRequest> requests) {
        if (requests == null || requests.isEmpty()) {
            throw badRequest("Список сообщений не должен быть пустым");
        }

        if (requests.size() > 10_000) {
            throw badRequest("За один запрос разрешено до 10000 сообщений");
        }

        requests.forEach(this::validateMessage);

        requests.stream()
                .map(CreateMessageRequest::authorId)
                .distinct()
                .forEach(this::requireUser);

        messages.saveAll(requests);

        return requests.size();
    }

    @Transactional
    public void delete(Long id) {
        requirePositiveId(id);

        if (messages.deleteById(id) == 0) {
            throw new ResponseStatusException(
                    HttpStatus.NOT_FOUND,
                    "Сообщение с ID " + id + " не найдено"
            );
        }
    }

    private void validateMessage(CreateMessageRequest request) {
        if (request == null
                || request.content() == null
                || request.content().isBlank()
                || request.content().length() > 255) {
            throw badRequest(
                    "content должен содержать от 1 до 255 символов"
            );
        }

        requirePositiveId(request.authorId());
    }

    private void requireUser(Long id) {
        requirePositiveId(id);

        users.findById(id).orElseThrow(
                () -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Пользователь с ID " + id + " не найден"
                )
        );
    }

    private void requirePositiveId(Long id) {
        if (id == null || id <= 0) {
            throw badRequest("ID должен быть положительным числом");
        }
    }

    private ResponseStatusException badRequest(String message) {
        return new ResponseStatusException(
                HttpStatus.BAD_REQUEST,
                message
        );
    }
}