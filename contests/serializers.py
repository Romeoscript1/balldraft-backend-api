# serializers.py
from rest_framework import serializers
from .models import ContestHistory, Player

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class ContestHistorySerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True)

    class Meta:
        model = ContestHistory
        fields = '__all__'

    def create(self, validated_data):
        players_data = validated_data.pop('players')
        contest_history = ContestHistory.objects.create(**validated_data)
        for player_data in players_data:
            player, created = Player.objects.get_or_create(id=player_data['id'], defaults=player_data)
            contest_history.players.add(player)
        return contest_history

    
    def update(self, instance, validated_data):
        players_data = validated_data.pop('players')
        instance.name = validated_data.get('name', instance.name)
        instance.fixture_id = validated_data.get('fixture_id', instance.fixture_id)
        instance.entry_amount = validated_data.get('entry_amount', instance.entry_amount)
        instance.action_title = validated_data.get('action_title', instance.action_title)
        instance.pending = validated_data.get('pending', instance.pending)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.total_points = validated_data.get('total_points', instance.total_points)
        instance.position = validated_data.get('position', instance.position)
        instance.won_amount = validated_data.get('won_amount', instance.won_amount)
        instance.pool_price = validated_data.get('pool_price', instance.pool_price)
        instance.save()

        existing_player_ids = set(instance.players.values_list('id', flat=True))
        new_player_ids = set()

        for player_data in players_data:
            player_id = player_data['id']
            new_player_ids.add(player_id)
            if player_id in existing_player_ids:
                player = Player.objects.get(id=player_id)
                player.name = player_data.get('name', player.name)
                player.image_url = player_data.get('image_url', player.image_url)
                player.team_id = player_data.get('team_id', player.team_id)
                player.fixture_id = player_data.get('fixture_id', player.fixture_id)
                player.points = player_data.get('points', player.points)
                player.position = player_data.get('position', player.position)
                player.save()
            else:
                player = Player.objects.create(**player_data)
                instance.players.add(player)

        for player_id in existing_player_ids - new_player_ids:
            instance.players.remove(Player.objects.get(id=player_id))

        return instance