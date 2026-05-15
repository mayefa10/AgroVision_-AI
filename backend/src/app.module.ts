import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { AuthModule } from './auth/auth.module';
import { UsersModule } from './users/users.module';
import { DashboardModule } from './dashboard/dashboard.module';
import { DatasetsModule } from './datasets/datasets.module';
import { PredictionsModule } from './predictions/predictions.module';
import { AlertsModule } from './alerts/alerts.module';
import { MapsModule } from './maps/maps.module';

@Module({
  imports: [AuthModule, UsersModule, DashboardModule, DatasetsModule, PredictionsModule, AlertsModule, MapsModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
