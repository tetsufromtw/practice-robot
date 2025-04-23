package position

import (
    "math/rand"
    "time"

    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/config"
    "github.com/tetsufromtw/practice-robot/robot-tracker/proto"
)

// Generator 位置生成器インターフェースを定義
type Generator interface {
    Generate() *proto.Position
}

// RandomGenerator ランダム位置生成を実装
type RandomGenerator struct {
    config *config.Config
}

// NewRandomGenerator 新しいランダム位置生成器を作成
func NewRandomGenerator(config *config.Config) *RandomGenerator {
    return &RandomGenerator{
        config: config,
    }
}

// Generate ランダムな位置を生成
func (g *RandomGenerator) Generate() *proto.Position {
    x := g.config.PositionMinX + rand.Float32()*(g.config.PositionMaxX-g.config.PositionMinX)
    y := g.config.PositionMinY + rand.Float32()*(g.config.PositionMaxY-g.config.PositionMinY)

    return &proto.Position{
        X:         x,
        Y:         y,
        Timestamp: time.Now().Unix(),
    }
}

// 初期化関数、ランダム数生成器に適切なシードを設定
func init() {
    rand.Seed(time.Now().UnixNano())
}