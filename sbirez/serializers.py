import json
import shlex
from sbirez import validation_helpers
from django.contrib.auth.models import User, Group
from sbirez.models import Topic, Reference, Phase, Keyword, Area, Firm, Person
from sbirez.models import Address, Workflow, Question, Proposal, Address, Element
from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    saved_topics = serializers.HyperlinkedRelatedField(many=True,
                                                       view_name='topics-detail',
                                                       read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('name', 'password', 'url', 'email', 'groups', 'saved_topics', 'firm')
        write_only_fields = ('password',)

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data.get('password'))
        # create an initial firm
        user.firm = Firm.objects.create(name=user.name)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.firm_id = validated_data.get('firm_id', instance.firm_id)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street', 'street2', 'city', 'state', 'zip')

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('name', 'title', 'email', 'phone', 'fax')

class FirmSerializer(serializers.HyperlinkedModelSerializer):
    address = AddressSerializer(required=False, many=False)
    point_of_contact = PersonSerializer(required=False, many=False)

    class Meta:
        model = Firm
        fields = ('id', 'name', 'tax_id', 'sbc_id', 'duns_id', 'cage_code',
                  'website', 'address', 'point_of_contact', 'founding_year',
                  'phase1_count', 'phase1_year', 'phase2_count',
                  'phase2_year', 'phase2_employees', 'current_employees',
                  'patent_count', 'total_revenue_range', 'revenue_percent')

    def update_user(self, firm_id):
        request = self.context.get('request', None)
        if request is not None and request.user.is_authenticated():
            user = get_user_model().objects.get(id=request.user.id)
            user.firm_id = firm_id
            user.save()

    def validate(self,data):
        return data

    def create(self, validated_data):
        if ('address' in validated_data):
            address_data = validated_data.pop('address')
            address = Address.objects.create(**address_data)
        else:
            address = None

        if ('point_of_contact' in validated_data):
            point_of_contact_data = validated_data.pop('point_of_contact')
            point_of_contact = Person.objects.create(**point_of_contact_data)
        else:
            point_of_contact = None
        firm = Firm.objects.create(point_of_contact=point_of_contact, address=address, **validated_data)
        self.update_user(firm.id)
        return firm

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.tax_id = validated_data.get('tax_id', instance.tax_id)
        instance.sbc_id = validated_data.get('sbc_id', instance.sbc_id)
        instance.duns_id = validated_data.get('duns_id', instance.duns_id)
        instance.cage_code = validated_data.get('cage_code', instance.cage_code)
        instance.website = validated_data.get('website', instance.website)
        instance.founding_year = validated_data.get('founding_year', instance.founding_year)
        instance.phase1_count = validated_data.get('phase1_count', instance.phase1_count)
        instance.phase1_year = validated_data.get('phase1_year', instance.phase1_year)
        instance.phase2_count = validated_data.get('phase2_count', instance.phase2_count)
        instance.phase2_year = validated_data.get('phase2_year', instance.phase2_year)
        instance.phase2_employees = validated_data.get('phase2_employees', instance.phase2_employees)
        instance.current_employees = validated_data.get('current_employees', instance.current_employees)
        instance.patent_count = validated_data.get('patent_count', instance.patent_count)
        instance.total_revenue_range = validated_data.get('total_revenue_range', instance.total_revenue_range)
        instance.revenue_percent = validated_data.get('revenue_percent', instance.revenue_percent)
        if ('point_of_contact' in validated_data):
            point_of_contact_data = validated_data.pop('point_of_contact')
            point_of_contact, created = Person.objects.get_or_create(id=instance.point_of_contact.id)
            if ('name' in point_of_contact_data):
                point_of_contact.name = point_of_contact_data['name']
            if ('title' in point_of_contact_data):
                point_of_contact.title = point_of_contact_data['title']
            if ('email' in point_of_contact_data):
                point_of_contact.email = point_of_contact_data['email']
            if ('phone' in point_of_contact_data):
                point_of_contact.phone = point_of_contact_data['phone']
            if ('fax' in point_of_contact_data):
                point_of_contact.fax = point_of_contact_data['fax']
            point_of_contact.save()
            instance.point_of_contact = point_of_contact

        if ('address' in validated_data):
            address_data = validated_data.pop('address')
            address, created = Address.objects.get_or_create(id=instance.address.id)
            if ('street' in address_data):
                address.street = address_data['street']
            if ('street2' in address_data):
                address.street2 = address_data['street2']
            if ('city' in address_data):
                address.city = address_data['city']
            if ('state' in address_data):
                address.state = address_data['state']
            if ('zip' in address_data):
                address.zip = address_data['zip']
            address.save()
            instance.address = address

        instance.save()
        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class AreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Area
        fields = ('area', )


class KeywordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Keyword
        fields = ('keyword', )


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ('phase', )


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = ('reference', )


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    references = ReferenceSerializer(many=True)
    phases = PhaseSerializer(many=True)
    keywords = KeywordSerializer(many=True)
    areas = AreaSerializer(many=True)
    saved = serializers.SerializerMethodField()

    def get_saved(self, obj):
        "``True`` if current has saved this topic for later reference.  ``None`` if no current user."

        current_user = self.context.get('request').user
        if current_user.is_anonymous():
            return None
        else:
            return obj.saved_by.filter(id=current_user.id).exists()

    class Meta:
        model = Topic
        fields = ('id', 'topic_number', 'solicitation_id', 'url', 'title', 'agency',
                    'program', 'description', 'objective', 'pre_release_date',
                    'proposals_begin_date', 'proposals_end_date', 'days_to_close',
                    'status'
                    , 'references', 'phases', 'keywords', 'areas',
                    'saved',
                    )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('name', 'order', 'data_type', 'required', 'default',
                  'human', 'help', 'validation', 'validation_msg', 'ask_if',
                  'subworkflow')


class WorkflowSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True)

    class Meta:
        model = Workflow
        fields = ('name', 'validation', 'questions', )


class ElementSerializer(serializers.ModelSerializer):

    # parent = serializers.PrimaryKeyRelatedField(read_only=True)
    # still nests

    # parent = serializers.IntegerField()
    # throws an error...

    class Meta:
        model = Element
        # exclude = ('parent', )
        # not compatible with `fields`, and simply excluding `parent`
        # leaves `children` out
        fields = ('id', 'name', 'order', 'element_type',
                  'required', 'default', 'human', 'help',
                  'validation', 'validation_msg', 'ask_if',
                  'children', 'parent', )
        # depth = 1
        # TODO: setting 'depth' to 1 works perfectly - except
        # that the nested children include 'parents' despite
        # being left out of `fields`!


def _validate_question(data, question):

    if question.required and not question.subworkflow:
        if (question.name not in data):
            raise serializers.ValidationError(
                'Required field %s absent' % question.name)
        if (hasattr(data[question.name], 'strip') and
            not data[question.name].strip()):
            raise serializers.ValidationError(
                'Required field %s absent' % question.name)

    if question.validation:
        for validation in question.validation.split(';'):
            args = shlex.split(validation)
            function_name = args.pop(0)
            try:
                func = getattr(validation_helpers, function_name)
            except AttributeError:
                # validation refers to a function not found in helper library
                # raise serializers.ValidationError(
                #    '%s: validation function %s absent from validation_helpers.py',
                #    question.name, function_name)
                continue
            if question.name in data:
                if not func(data, data[question.name], *args):
                    raise serializers.ValidationError(
                        '%s: %s' % (question.name, question.validation_msg))

    if question.subworkflow:
        for subquestion in question.subworkflow.questions.all():
            _validate_question(data, subquestion)

    # TODO: gather all the validation errors
    # TODO: allow validate-but-not-check-required, no-validate

def genericValidator(proposal):
    '''
    Inspect the workflow's validators and apply them to
    the proposal's data
    '''
    data = json.loads(proposal['data'])

    for question in proposal['workflow'].questions.all():
        _validate_question(data, question)


class ProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        validators = [genericValidator]

    # def validate(self, attrs):
        # TODO: use self.context['request'].method (?) to toggle validation
        # return the validated data: genericValidator(proposal=attrs)


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

