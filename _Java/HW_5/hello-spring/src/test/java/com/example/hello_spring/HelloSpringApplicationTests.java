package com.example.hello_spring;

import java.util.UUID;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.notNullValue;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class HelloSpringApplicationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void getMessagesEndpointReturnsPage() throws Exception {
        Long authorId = createTestUser();

        insertMessage("Первое сообщение", authorId);
        insertMessage("Второе сообщение", authorId);

        mockMvc.perform(
                        get("/api/messages")
                                .contextPath("/api")
                                .param("authorId", authorId.toString())
                                .param("page", "0")
                                .param("size", "10")
                )
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(2)))
                .andExpect(jsonPath("$.content[0].id", notNullValue()))
                .andExpect(jsonPath("$.content[0].content")
                        .value("Второе сообщение"))
                .andExpect(jsonPath("$.content[1].content")
                        .value("Первое сообщение"))
                .andExpect(jsonPath("$.page").value(0))
                .andExpect(jsonPath("$.size").value(10))
                .andExpect(jsonPath("$.totalElements").value(2))
                .andExpect(jsonPath("$.totalPages").value(1));
    }

    @Test
    void postMessagesEndpointCreatesNewMessage() throws Exception {
        Long authorId = createTestUser();

        String jsonPayload = """
                {
                  "content": "New message via POST",
                  "authorId": %d
                }
                """.formatted(authorId);

        mockMvc.perform(
                        post("/api/messages")
                                .contextPath("/api")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(jsonPayload)
                )
                .andDo(print())
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.content")
                        .value("New message via POST"));

        mockMvc.perform(
                        get("/api/messages")
                                .contextPath("/api")
                                .param("authorId", authorId.toString())
                                .param("page", "0")
                                .param("size", "10")
                )
                .andDo(print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(1)))
                .andExpect(jsonPath("$.content[0].content")
                        .value("New message via POST"))
                .andExpect(jsonPath("$.totalElements").value(1));
    }

    private Long createTestUser() {
        String username = "test-" + UUID.randomUUID();

        return jdbcTemplate.queryForObject(
                """
                INSERT INTO users (username)
                VALUES (?)
                RETURNING id
                """,
                Long.class,
                username
        );
    }

    private void insertMessage(String content, Long authorId) {
        jdbcTemplate.update(
                """
                INSERT INTO messages (content, author_id)
                VALUES (?, ?)
                """,
                content,
                authorId
        );
    }
}