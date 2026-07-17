import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.enableCors({
    origin: [
      "http://localhost:3000", // desarrollo
      process.env.FRONTEND_URL || "",
    ],
    credentials: true,
  });

  await app.listen(process.env.PORT || 4000);

  console.log(`🚀 Backend running on port ${process.env.PORT || 4000}`);
}

bootstrap();
