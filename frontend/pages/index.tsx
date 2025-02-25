import { Box, Button, Container, Flex, Heading, Text, useColorModeValue } from '@chakra-ui/react';
import { FaRobot, FaVolumeUp, FaUser } from 'react-icons/fa';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';
import React from 'react';

export default function Home() {
  const router = useRouter();
  
  const bgGradient = useColorModeValue(
    'linear(to-br, purple.500, pink.400)',
    'linear(to-br, purple.700, pink.600)'
  );
  
  const cardBg = useColorModeValue('white', 'gray.800');
  
  return (
    <>
      <Head>
        <title>AI Anime Companion</title>
        <meta name="description" content="Interactive AI-powered anime companion with voice synthesis and Live2D animations" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Box 
        as="main" 
        minH="100vh" 
        bgGradient={bgGradient}
      >
        {/* Hero Section */}
        <Container maxW="container.xl" pt={20} pb={20}>
          <Flex 
            direction={{ base: 'column', md: 'row' }} 
            align="center" 
            justify="space-between"
            mb={20}
          >
            <Box maxW={{ base: '100%', md: '50%' }} mb={{ base: 10, md: 0 }}>
              <Heading 
                as="h1" 
                size="3xl" 
                color="white" 
                lineHeight={1.2}
                mb={6}
              >
                Your AI Anime Companion
              </Heading>
              <Text 
                fontSize="xl" 
                color="whiteAlpha.900" 
                mb={8}
              >
                Create custom AI companions with anime-style voices and Live2D animations. 
                Personalize their knowledge, personality, and appearance.
              </Text>
              <Button 
                size="lg" 
                colorScheme="whiteAlpha" 
                onClick={() => router.push('/dashboard')}
                mr={4}
              >
                Get Started
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                colorScheme="whiteAlpha"
                onClick={() => router.push('/about')}
              >
                Learn More
              </Button>
            </Box>
            
            <Box 
              w={{ base: '100%', md: '45%' }} 
              h={{ base: '300px', md: '400px' }}
              bg="rgba(0,0,0,0.2)" 
              borderRadius="lg"
              position="relative"
              overflow="hidden"
            >
              {/* This would be replaced with actual Live2D preview */}
              <Flex 
                justify="center" 
                align="center" 
                h="100%" 
                color="white"
                flexDir="column"
              >
                <FaRobot size={80} />
                <Text mt={4} fontSize="lg">Live2D Preview</Text>
              </Flex>
            </Box>
          </Flex>

          {/* Features Section */}
          <Heading as="h2" size="xl" color="white" textAlign="center" mb={10}>
            Features
          </Heading>
          
          <Flex 
            direction={{ base: 'column', md: 'row' }} 
            justify="space-between"
            gap={6}
          >
            {/* Feature 1 */}
            <Box 
              bg={cardBg} 
              p={8} 
              borderRadius="lg" 
              flex="1" 
              boxShadow="xl"
            >
              <Flex 
                w={12} 
                h={12} 
                bg="purple.500" 
                borderRadius="full" 
                justify="center" 
                align="center"
                color="white"
                mb={4}
              >
                <FaRobot size={24} />
              </Flex>
              <Heading as="h3" size="md" mb={4}>
                Custom AI Personality
              </Heading>
              <Text>
                Design your companion&apos;s personality, memories, knowledge base, and behavioral traits. Upload documents to create specialized knowledge.
              </Text>
            </Box>
            
            {/* Feature 2 */}
            <Box 
              bg={cardBg} 
              p={8} 
              borderRadius="lg" 
              flex="1" 
              boxShadow="xl"
            >
              <Flex 
                w={12} 
                h={12} 
                bg="pink.500" 
                borderRadius="full" 
                justify="center" 
                align="center"
                color="white"
                mb={4}
              >
                <FaVolumeUp size={24} />
              </Flex>
              <Heading as="h3" size="md" mb={4}>
                Anime Voice Synthesis
              </Heading>
              <Text>
                Choose from a variety of anime-style voices or create a custom voice. Responses are spoken aloud with natural-sounding intonation.
              </Text>
            </Box>
            
            {/* Feature 3 */}
            <Box 
              bg={cardBg} 
              p={8} 
              borderRadius="lg" 
              flex="1" 
              boxShadow="xl"
            >
              <Flex 
                w={12} 
                h={12} 
                bg="purple.500" 
                borderRadius="full" 
                justify="center" 
                align="center"
                color="white"
                mb={4}
              >
                <FaUser size={24} />
              </Flex>
              <Heading as="h3" size="md" mb={4}>
                Live2D Animation
              </Heading>
              <Text>
                Watch your companion come to life with expressive Live2D animations. Synchronized lip movements and facial expressions add realism.
              </Text>
            </Box>
          </Flex>
        </Container>
        
        {/* Footer */}
        <Box py={6} bg="rgba(0,0,0,0.3)" color="white">
          <Container maxW="container.xl">
            <Flex 
              direction={{ base: 'column', md: 'row' }} 
              justify="space-between"
              align="center"
            >
              <Text>&copy; {new Date().getFullYear()} AI Anime Companion</Text>
              <Flex gap={6}>
                <Link href="/about">About</Link>
                <Link href="/privacy">Privacy</Link>
                <Link href="/terms">Terms</Link>
              </Flex>
            </Flex>
          </Container>
        </Box>
      </Box>
    </>
  );
} 