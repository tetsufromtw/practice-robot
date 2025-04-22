package service

import (
    "time"

    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/config"
    "github.com/tetsufromtw/practice-robot/robot-tracker/internal/position"
    "github.com/tetsufromtw/practice-robot/robot-tracker/pkg/logger"
    "github.com/tetsufromtw/practice-robot/robot-tracker/proto"
)

// RobotTrackerService 實現 gRPC 服務
type RobotTrackerService struct {
    proto.UnimplementedRobotTrackerServer
    config    *config.Config
    generator position.Generator
    logger    logger.Logger
}

// NewRobotTrackerService 創建新的跟踪服務實例
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

// TrackRobot 實現 gRPC 流式服務，定期發送機器人位置
func (s *RobotTrackerService) TrackRobot(req *proto.TrackRequest, stream proto.RobotTracker_TrackRobotServer) error {
    s.logger.Info("開始追蹤機器人位置")

    ticker := time.NewTicker(time.Duration(s.config.UpdateFrequency) * time.Millisecond)
    defer ticker.Stop()

    // 優雅關閉處理
    done := stream.Context().Done()

    for {
        select {
        case <-done:
            s.logger.Info("客戶端連接已關閉")
            return nil
        case <-ticker.C:
            // 產生新位置
            position := s.generator.Generate()

            // 發送位置資訊
            if err := stream.Send(position); err != nil {
                s.logger.Error("發送位置時出錯: %v", err)
                return err
            }

            s.logger.Debug("發送位置: x=%v, y=%v, timestamp=%v", position.X, position.Y, position.Timestamp)
        }
    }
}