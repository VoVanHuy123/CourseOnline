-- Create PaymentHistory table for tracking payment details
CREATE TABLE IF NOT EXISTS payment_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_day DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_day DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    order_id VARCHAR(100) NOT NULL UNIQUE,
    payment_method VARCHAR(50) NOT NULL,
    amount FLOAT NOT NULL,
    payment_status BOOLEAN DEFAULT FALSE,
    transaction_id VARCHAR(100),
    payment_date DATETIME,
    response_code VARCHAR(10),
    response_message TEXT,
    enrollment_id INT,
    user_id INT,
    course_id INT,
    FOREIGN KEY (enrollment_id) REFERENCES enrollment(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE
);
