package config

// Config 保存應用程式配置
type Config struct {
    Port            string
    PositionMinX    float32
    PositionMaxX    float32
    PositionMinY    float32
    PositionMaxY    float32
    UpdateFrequency int // 毫秒
}

// NewDefaultConfig 返回帶有預設值的配置
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