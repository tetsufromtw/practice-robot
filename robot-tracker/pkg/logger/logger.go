package logger

import (
    "log"
    "os"
)

// Logger ログインターフェースを定義
type Logger interface {
    Info(format string, v ...interface{})
    Error(format string, v ...interface{})
    Debug(format string, v ...interface{})
}

// SimpleLogger 基本的なログ機能を実装
type SimpleLogger struct {
    infoLogger  *log.Logger
    errorLogger *log.Logger
    debugLogger *log.Logger
}

// NewSimpleLogger 新しいシンプルなログインスタンスを作成
func NewSimpleLogger() *SimpleLogger {
    return &SimpleLogger{
        infoLogger:  log.New(os.Stdout, "INFO: ", log.Ldate|log.Ltime),
        errorLogger: log.New(os.Stderr, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile),
        debugLogger: log.New(os.Stdout, "DEBUG: ", log.Ldate|log.Ltime|log.Lshortfile),
    }
}

// Info 情報レベルのログを記録
func (l *SimpleLogger) Info(format string, v ...interface{}) {
    l.infoLogger.Printf(format, v...)
}

// Error エラーレベルのログを記録
func (l *SimpleLogger) Error(format string, v ...interface{}) {
    l.errorLogger.Printf(format, v...)
}

// Debug デバッグレベルのログを記録
func (l *SimpleLogger) Debug(format string, v ...interface{}) {
    l.debugLogger.Printf(format, v...)
}