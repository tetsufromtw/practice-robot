package position

import (
    "math/rand"
    "time"

    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/config"
    "github.com/tetsufromtw/practice-robot/robot-tracker/proto"
)

// Generator 定義位置生成器介面
type Generator interface {
    Generate() *proto.Position
}

// RandomGenerator 實現隨機位置生成
type RandomGenerator struct {
    config *config.Config
}

// NewRandomGenerator 創建新的隨機位置生成器
func NewRandomGenerator(config *config.Config) *RandomGenerator {
    return &RandomGenerator{
        config: config,
    }
}

// Generate 產生隨機位置
func (g *RandomGenerator) Generate() *proto.Position {
    x := g.config.PositionMinX + rand.Float32()*(g.config.PositionMaxX-g.config.PositionMinX)
    y := g.config.PositionMinY + rand.Float32()*(g.config.PositionMaxY-g.config.PositionMinY)

    return &proto.Position{
        X:         x,
        Y:         y,
        Timestamp: time.Now().Unix(),
    }
}

// 初始化函數，確保隨機數生成器有合適的種子
func init() {
    rand.Seed(time.Now().UnixNano())
}