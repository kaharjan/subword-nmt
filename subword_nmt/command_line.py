import io
import sys
import codecs
import argparse

from subword_nmt.learn_bpe import learn_bpe
from subword_nmt.apply_bpe import BPE, read_vocabulary
from subword_nmt.get_vocab import get_vocab
from subword_nmt.segment_char_ngrams import segment_char_ngrams
from subword_nmt.learn_joint_bpe_and_vocab import learn_joint_bpe_and_vocab

from subword_nmt.learn_bpe import create_parser as create_learn_bpe_parser
from subword_nmt.apply_bpe import create_parser as create_apply_bpe_parser
from subword_nmt.get_vocab import create_parser as create_get_vocab_parser
from subword_nmt.learn_joint_bpe_and_vocab import create_parser as create_learn_joint_bpe_and_vocab_parser
from subword_nmt.segment_char_ngrams import create_parser as create_segment_char_ngrams_parser

# hack for python2/3 compatibility
argparse.open = io.open

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="subword-nmt segmentation")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    learn_bpe_parser = create_learn_bpe_parser(subparsers)
    apply_bpe_parser = create_apply_bpe_parser(subparsers)
    get_vocab_parser = create_get_vocab_parser(subparsers)
    segment_char_ngrams_parser = create_segment_char_ngrams_parser(subparsers)
    learn_joint_bpe_and_vocab_parser = create_learn_joint_bpe_and_vocab_parser(subparsers)

    args = parser.parse_args()

    if args.command == 'learn-bpe':
        # read/write files as UTF-8
        if args.input.name != '<stdin>':
            args.input = codecs.open(args.input.name, encoding='utf-8')
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        learn_bpe(args.input, args.output, args.symbols, args.min_frequency, args.verbose, is_dict=args.dict_input)
    elif args.command == 'apply-bpe':
        # read/write files as UTF-8
        args.codes = codecs.open(args.codes.name, encoding='utf-8')
        if args.input.name != '<stdin>':
            args.input = codecs.open(args.input.name, encoding='utf-8')
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')
        if args.vocabulary:
            args.vocabulary = codecs.open(args.vocabulary.name, encoding='utf-8')

        if args.vocabulary:
            vocabulary = read_vocabulary(args.vocabulary, args.vocabulary_threshold)
        else:
            vocabulary = None

        bpe = BPE(args.codes, args.merges, args.separator, vocabulary, args.glossaries)

        for line in args.input:
            args.output.write(bpe.process_line(line))

    elif args.command == 'get-vocab':
        if args.train_file.name != '<stdin>':
            args.train_file = codecs.open(args.train_file.name, encoding='utf-8')
        if args.vocab_file.name != '<stdout>':
            args.vocab_file = codecs.open(args.vocab_file.name, 'w', encoding='utf-8')
        get_vocab(args.train_file, args.vocab_file)
    elif args.command == 'segment-char-ngrams':
        segment_char_ngrams(args)
    elif args.command == 'learn-joint-bpe-and-vocab':
        learn_joint_bpe_and_vocab(args)
    else:
        raise Exception('Invalid command provided')


if __name__ == '__main__':
    # python 2/3 compatibility
    if sys.version_info < (3, 0):
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
        sys.stdin = codecs.getreader('UTF-8')(sys.stdin)
    else:
        sys.stderr = codecs.getwriter('UTF-8')(sys.stderr.buffer)
        sys.stdout = codecs.getwriter('UTF-8')(sys.stdout.buffer)
        sys.stdin = codecs.getreader('UTF-8')(sys.stdin.buffer)

    main()