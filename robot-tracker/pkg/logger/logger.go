package logger

import (
    "log"
    "os"
)

// Logger 定義日誌介面
type Logger interface {
    Info(format string, v ...interface{})
    Error(format string, v ...interface{})
    Debug(format string, v ...interface{})
}

// SimpleLogger 實現基本日誌功能
type SimpleLogger struct {
    infoLogger  *log.Logger
    errorLogger *log.Logger
    debugLogger *log.Logger
}

// NewSimpleLogger 創建新的簡單日誌實例
func NewSimpleLogger() *SimpleLogger {
    return &SimpleLogger{
        infoLogger:  log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime),
        errorLogger: log.New(os.Stderr, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile),
        debugLogger: log.New(os.Stdout, "DEBUG: ", log.Ldate|log.Ltime|log.Lshortfile),
    }
}

// Info 記錄信息級別日誌
func (l *SimpleLogger) Info(format string, v ...interface{}) {
    l.infoLogger.Printf(format, v...)
}

// Error 記錄錯誤級別日誌
func (l *SimpleLogger) Error(format string, v ...interface{}) {
    l.errorLogger.Printf(format, v...)
}

// Debug 記錄調試級別日誌
func (l *SimpleLogger) Debug(format string, v ...interface{}) {
    l.debugLogger.Printf(format, v...)
}