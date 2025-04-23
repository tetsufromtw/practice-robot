package service

import (
    "time"

    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/config"
    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/position"
    "github.com/tetsufromtw/practice-robot/robot-tracker/pkg/logger"
    "github.com/tetsufromtw/practice-robot/robot-tracker/proto"
)

// RobotTrackerService gRPCサービスを実装
type RobotTrackerService struct {
    proto.UnimplementedRobotTrackerServer
    config    *config.Config
    generator position.Generator
    logger    logger.Logger
}

// NewRobotTrackerService 新しいトラッキングサービスインスタンスを作成
func NewRobotTrackerService(
    config *config.Config,
    generator position.Generator,
    logger logger.Logger,
) *RobotTrackerService {
    return &RobotTrackerService{
        config:    config,
        generator: generator,
        logger:    logger,
    }
}

// TrackRobot gRPCストリーミングサービスを実装し、定期的にロボットの位置を送信
func (s *RobotTrackerService) TrackRobot(req *proto.TrackRequest, stream proto.RobotTracker_TrackRobotServer) error {
    s.logger.Info("ロボット位置の追跡を開始")

    ticker := time.NewTicker(time.Duration(s.config.UpdateFrequency) * time.Millisecond)
    defer ticker.Stop()

    // 優雅なシャットダウン処理
    done := stream.Context().Done()

    for {
        select {
        case <-done:
            s.logger.Info("クライアント接続が閉じられました")
            return nil
        case <-ticker.C:
            // 新しい位置を生成
            position := s.generator.Generate()

            // 位置情報を送信
            if err := stream.Send(position); err != nil {
                s.logger.Error("位置送信中にエラーが発生: %v", err)
                return err
            }

            s.logger.Debug("位置を送信: x=%v, y=%v, timestamp=%v", position.X, position.Y, position.Timestamp)
        }
    }
}