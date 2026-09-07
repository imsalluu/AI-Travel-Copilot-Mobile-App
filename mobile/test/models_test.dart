import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/data/models/user_model.dart';
import 'package:mobile/data/models/trip_model.dart';
import 'package:mobile/data/models/chat_model.dart';
import 'package:mobile/data/models/weather_model.dart';
import 'package:mobile/data/models/budget_model.dart';

void main() {
  group('Mobile Data Models Unit Tests', () {
    test('UserModel serialization and deserialization', () {
      final json = {
        'id': 'user-123',
        'email': 'traveler@test.com',
        'full_name': 'Salman Khan',
        'home_country': 'Bangladesh',
        'home_currency': 'BDT',
      };
      final user = UserModel.fromJson(json);
      expect(user.id, 'user-123');
      expect(user.email, 'traveler@test.com');
      expect(user.fullName, 'Salman Khan');
      expect(user.homeCurrency, 'BDT');
    });

    test('TripModel with days and activities serialization', () {
      final json = {
        'id': 'trip-1',
        'user_id': 'user-123',
        'title': "3-Day Cox's Bazar Tour",
        'destination': "Cox's Bazar",
        'start_date': '2026-10-01',
        'end_date': '2026-10-03',
        'duration_days': 3,
        'total_budget': 20000.0,
        'currency': 'BDT',
        'days': [
          {
            'id': 'day-1',
            'trip_id': 'trip-1',
            'day_number': 1,
            'date': '2026-10-01',
            'title': 'Arrival & Beach Sunset',
            'activities': [
              {
                'id': 'act-1',
                'trip_day_id': 'day-1',
                'title': 'Laboni Beach Sunset',
                'location_name': 'Laboni Beach',
                'category': 'beach',
                'estimated_cost': 250.0,
              }
            ]
          }
        ]
      };
      final trip = TripModel.fromJson(json);
      expect(trip.destination, "Cox's Bazar");
      expect(trip.days.length, 1);
      expect(trip.days.first.activities.first.title, 'Laboni Beach Sunset');
    });

    test('ChatMessageModel parsing with structured itinerary card', () {
      final json = {
        'id': 'msg-1',
        'conversation_id': 'conv-1',
        'role': 'assistant',
        'content': 'Here is your plan',
        'message_type': 'itinerary_card',
        'structured_data': {
          'destination': "Cox's Bazar",
          'duration_days': 3,
          'total_budget': 20000.0,
        },
        'created_at': DateTime.now().toIso8601String(),
      };
      final msg = ChatMessageModel.fromJson(json);
      expect(msg.messageType, 'itinerary_card');
      expect(msg.structuredData?['destination'], "Cox's Bazar");
    });
  });
}
