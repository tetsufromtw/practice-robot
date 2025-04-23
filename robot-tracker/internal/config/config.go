package config

// Config アプリケーション設定を保存する
type Config struct {
    Port            string
    PositionMinX    float32
    PositionMaxX    float32
    PositionMinY    float32
    PositionMaxY    float32
    UpdateFrequency int // ミリ秒
}

// NewDefaultConfig デフォルト値を持つ設定を返す
func NewDefaultConfig() *Config {
    return &Config{
        Port:            "50051",
        PositionMinX:    0,
        PositionMaxX:    100,
        PositionMinY:    0,
        PositionMaxY:    100,
        UpdateFrequency: 1000, // 1秒
    }
}